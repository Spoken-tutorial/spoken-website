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
  private id: number;
  private scriptId: number;
  private orderId: number;
  public oldData: any = [];
  public newData: any = [];
  public removedData: any = [];

  constructor(
    private route: ActivatedRoute,
    public createscriptService: CreateScriptService,
    public router: Router
  ) { }

  public onSaveScript(script: any) {
    if (script['cue'] == '' || script['narration'] == '' ) {
      // console.log(script)
      // Do nothing
    }
    else {
      if (script['id'] == '') {
        script['order'] = this.orderId + 1;
        script['script'] = this.scriptId;
        this.orderId = this.orderId + 1;
        // console.log(script)

        this.createscriptService.postScript(
          this.id,
          {
            "details": [script]
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
          this.id, script
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
      this.slides.push(
        {
          id: '',
          cue: '',
          narration: '',
          order: '',
          script: ''
        }
      );
   
    }
   
  }

  public getData() {
    this.createscriptService.getScript(this.id).subscribe(
      (res) => {
        this.slides = res;
        this.scriptId = this.slides[0]['script'];
        this.orderId = this.slides[this.slides.length - 1]['order'];
      }
    );
  }

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
    this.getData();
  }

}