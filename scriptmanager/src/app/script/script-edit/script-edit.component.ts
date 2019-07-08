import { Component, OnInit, Input } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { CreateScriptService } from '../../_service/create-script.service';
import * as Noty from 'noty';

@Component({
  selector: 'app-script-edit',
  templateUrl: './script-edit.component.html',
  styleUrls: ['./script-edit.component.sass']
})

export class ScriptEditComponent implements OnInit {
  public slides: any = [];
  private tid: number;
  private lid: number;
  private scriptId: number;
  private orderId: number;

  constructor(
    private route: ActivatedRoute,
    public createscriptService: CreateScriptService,
    public router: Router
  ) { }

  // argument:contains the data of the cue and narration which is entered by the user while creating the script
  // what it does:takes the data and make an api call(POST request) so as to save that data to database
  // returns: status==success if data is saved successfully and status=false if data couldn't saved successfully because of some reason 
  public onSaveScript(script: any) {
    if (script['cue'] == '' || script['narration'] == '') {
      return // Do nothing
    }
    
    else {
      if (script['fid'] == '') {
        script['order'] = this.orderId + 1;
        script['script'] = this.scriptId;
        this.orderId = this.orderId + 1;
        // console.log(script)

        this.createscriptService.postScript(
          this.tid, this.lid,
          {
            "details": [script],
            "type" : 'form'
          }
        ).subscribe(
          (res) => {
            new Noty({
              type: 'success',
              layout: 'topRight',
              theme: 'metroui',
              closeWith: ['click'],
              text: 'The script is sucessfully updated!',
              animation: {
                open: 'animated fadeInRight',
                close: 'animated fadeOutRight'
              },
              timeout: 4000,
              killer: true
            }).show();
          },
          (error) => {
            new Noty({
              type: 'error',
              layout: 'topRight',
              theme: 'metroui',
              closeWith: ['click'],
              text: 'Woops! There seems to be an error.',
              animation: {
                open: 'animated fadeInRight',
                close: 'animated fadeOutRight'
              },
              timeout: 4000,
              killer: true
            }).show();
          }
        );
      }

      else {
        this.createscriptService.patchScript(
          this.tid, this.lid, script
        ).subscribe(
          (res) => {
            new Noty({
              type: 'success',
              layout: 'topRight',
              theme: 'metroui',
              closeWith: ['click'],
              text: 'The script is sucessfully updated!',
              animation: {
                open: 'animated fadeInRight',
                close: 'animated fadeOutRight'
              },
              timeout: 4000,
              killer: true
            }).show();
          },
          (error) => {
            new Noty({
              type: 'error',
              layout: 'topRight',
              theme: 'metroui',
              closeWith: ['click'],
              text: 'Woops! There seems to be an error.',
              animation: {
                open: 'animated fadeInRight',
                close: 'animated fadeOutRight'
              },
              timeout: 4000,
              killer: true
            }).show();
          }
        );
      }

    }

  }

  // argument:tutorial id and 
  // what it does:
  // returns: status==success if data is saved successfully and status=false if data couldn't saved successfully because of some reason 
  public getData() {
    this.createscriptService.getScript(this.tid, this.lid).subscribe(
      (res) => {
        this.slides = res;
        this.scriptId = this.slides[0]['script'];
        this.orderId = this.slides[this.slides.length - 1]['order'];
      }
    );
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.tid = +params['tid'];//tid is tutorial id
    });
    this.lid = this.route.snapshot.params['lid']//lid is language id

    this.getData();
  }

}