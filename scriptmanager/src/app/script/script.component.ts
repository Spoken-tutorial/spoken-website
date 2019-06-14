import { Component, OnInit, Input, Output, EventEmitter } from '@angular/core';
import {Router} from "@angular/router";
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-script',
  templateUrl: './script.component.html',
  styleUrls: ['./script.component.sass']
})
export class ScriptComponent implements OnInit {
  @Input() slides: any;
  @Output() onSaveScript = new EventEmitter<any>();
  @Input() removedData: any;
  @Input() nav:any;
  public id;

  constructor(public router:Router,public route:ActivatedRoute) { }

  public addSlide() {
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

  public onRemoveSlide(index) {
    if ( this.slides[index]['id'] != '' ) {
    this.removedData.push(this.slides[index]['id'])
    };
    this.slides.splice(index, 1);
  }

  public saveScript() {
    this.onSaveScript.emit(this.slides); 
  }

  ngOnInit() {
    this.addSlide();
    this.route.params.subscribe(params => {
      this.id = +params['id'];
    });
  }

}
