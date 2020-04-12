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
  private tid: number; // tutorial id
  private lid: number; // language id
  private vid: number; // version id
  private scriptId: number;
  private orderId: number;

  constructor(
    private route: ActivatedRoute,
    public createscriptService: CreateScriptService,
    public router: Router
  ) { }

  public getRelativeOrdering() {
    var relative_ordering = [];

    for (var i = 0; i < this.slides.length; i++) {
      const slide = this.slides[i];
      relative_ordering.push(slide.id);
    }

    return relative_ordering;
  }

  // argument:contains the data of the cue and narration which is entered by the user while creating the script
  // what it does:takes the data and make an api call(POST request) so as to save that data to database
  // returns: status==success if data is saved successfully and status=false if data couldn't saved successfully because of some reason 
  public onSaveScript(script: any) {
    this.createscriptService.patchScript(
      this.tid, this.lid, this.vid, script
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

  public onInsertSlide(index) {
    var script = this.slides[index];

    script['order'] = index + 1;
    script['script'] = this.scriptId;

    this.orderId = this.orderId + 1;
    // var relative_ordering = this.getRelativeOrdering().join(',');

    this.createscriptService.postScript(
      this.tid, this.lid, this.vid,
      {
        "details": [script],
        // "ordering": relative_ordering,
        "prevSlideID": this.slides[index-1].id,
        "type": 'form'
      }
    ).subscribe(
      (res) => {
        this.slides[index] = res['data'][0];
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

  public onDuplicateSlide(index) {
    this.onInsertSlide(index);
  }

  // argument:tutorial id and 
  // what it does:
  // returns: status==success if data is saved successfully and status=false if data couldn't saved successfully because of some reason 
  public getData() {
    this.createscriptService.getScript(this.tid, this.lid, this.vid).subscribe(
      (res) => {
        this.slides = res['slides'];
        const published = res['status'];

        if (published) {
          this.router.navigate(['']);
        }
        
        if (!res['editable']) {
          this.router.navigate(['']);
        }

        if (this.slides.length == 0) return;

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
    this.vid = this.route.snapshot.params['vid']//version id
    this.orderId = 0;
    this.getData();
  }

}